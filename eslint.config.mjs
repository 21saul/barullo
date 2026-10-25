import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Las herramientas de `scripts/` son CommonJS de Node, no van al bundle:
    // la regla de `require()` no aplica.
    "scripts/**",
    // `remotion/` es otro proyecto, con su propio package.json y sus reglas.
    "remotion/**",
  ]),
]);

export default eslintConfig;
