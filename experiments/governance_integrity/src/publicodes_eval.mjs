#!/usr/bin/env node
// Native Publicodes runtime adapter.
//
// Loads a rule tree exactly the way mon-entreprise's own build does
// (@publicodes/tools getModelFromSource over one or more `règles` directories),
// then builds a publicodes Engine and answers one of three requests:
//   build      -> rule counts (proves the tree parses with the real engine)
//   list       -> dotted rule names, optionally filtered by prefix
//   evaluate   -> evaluate rules for a situation (JSON) and print nodeValue/unit
//
// Usage (all output is one JSON object on stdout):
//   node publicodes_eval.mjs build    --rules DIR [--rules DIR2]
//   node publicodes_eval.mjs list     --rules DIR [--prefix "dirigeant . auto-entrepreneur"]
//   node publicodes_eval.mjs evaluate --rules DIR --situation '{"date":"01/07/2024", ...}' --rule "a . b" [--rule "c . d"]
//   node publicodes_eval.mjs evaluate --rules DIR --spec FILE.json   (spec = {situation:{}, rules:[...]})
//
// Nothing here interprets law. It only runs the organisation's own semantic
// definitions through the organisation's own engine.

import { readFileSync } from 'node:fs'
import path from 'node:path'
import Engine from 'publicodes'
import { getModelFromSource } from '@publicodes/tools/compilation'

function parseArgs(argv) {
  const out = { rules: [], rule: [], situation: null, prefix: null, spec: null, cmd: argv[0] }
  for (let i = 1; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--rules') out.rules.push(path.resolve(argv[++i]))
    else if (a === '--rule') out.rule.push(argv[++i])
    else if (a === '--situation') out.situation = JSON.parse(argv[++i])
    else if (a === '--prefix') out.prefix = argv[++i]
    else if (a === '--spec') out.spec = argv[++i]
    else throw new Error(`unknown argument ${a}`)
  }
  if (!out.rules.length) throw new Error('--rules DIR is required')
  return out
}

function silence(fn) {
  // getModelFromSource(verbose:false) is quiet, but publicodes prints deprecation
  // warnings for old rule syntax on stderr; keep stdout clean for JSON.
  const w = console.warn, l = console.log
  console.warn = () => {}
  console.log = () => {}
  try { return fn() } finally { console.warn = w; console.log = l }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  // @publicodes/tools 1.0.7 takes one source directory; newer mon-entreprise builds
  // pass several (modele-ti + modele-commun) and merge. Merge here the same way,
  // refusing silently overwritten rule names.
  const rules = {}
  for (const dir of args.rules) {
    const part = silence(() => getModelFromSource(dir, { verbose: false }))
    for (const [name, def] of Object.entries(part)) {
      if (name in rules) throw new Error(`rule "${name}" defined in more than one source directory`)
      rules[name] = def
    }
  }
  const engine = silence(() => new Engine(rules))
  const parsed = engine.getParsedRules()
  const result = { command: args.cmd, rules_dirs: args.rules, raw_rule_count: Object.keys(rules).length, parsed_rule_count: Object.keys(parsed).length }
  if (args.cmd === 'build') {
    // nothing more: a successful parse is the native syntax check
  } else if (args.cmd === 'list') {
    result.names = Object.keys(parsed).filter(n => !args.prefix || n.startsWith(args.prefix))
  } else if (args.cmd === 'evaluate') {
    let situation = args.situation || {}
    let names = args.rule
    if (args.spec) {
      const spec = JSON.parse(readFileSync(args.spec, 'utf8'))
      situation = spec.situation || situation
      names = names.concat(spec.rules || [])
    }
    result.situation = situation
    result.evaluations = {}
    try {
      silence(() => engine.setSituation(situation))
    } catch (e) {
      result.situation_error = String(e.message).split('\n').filter(Boolean).slice(0, 3).join(' | ')
    }
    for (const name of names) {
      try {
        const ev = silence(() => engine.evaluate(name))
        const missing = ev.missingVariables ? Object.keys(ev.missingVariables) : []
        result.evaluations[name] = { nodeValue: ev.nodeValue === undefined ? null : ev.nodeValue, unit: ev.unit ? (ev.unit.numerators || []).join('.') + (ev.unit.denominators && ev.unit.denominators.length ? '/' + ev.unit.denominators.join('.') : '') : null, missing_variables: missing.slice(0, 12), missing_count: missing.length }
      } catch (e) {
        result.evaluations[name] = { error: String(e.message).split('\n').filter(Boolean).slice(0, 3).join(' | ') }
      }
    }
  } else {
    throw new Error(`unknown command ${args.cmd}; use build | list | evaluate`)
  }
  process.stdout.write(JSON.stringify(result, null, 1) + '\n')
}

try { main() } catch (e) { process.stdout.write(JSON.stringify({ error: String(e.message) }) + '\n'); process.exit(1) }
