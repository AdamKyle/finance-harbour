import importAlias from '@dword-design/eslint-plugin-import-alias';
import eslint from '@eslint/js';
import stylistic from '@stylistic/eslint-plugin';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import importPlugin from 'eslint-plugin-import';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettierPlugin from 'eslint-plugin-prettier';
import reactHooks from 'eslint-plugin-react-hooks';
import unusedImports from 'eslint-plugin-unused-imports';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dirname = path.dirname(fileURLToPath(import.meta.url));

export default [
  importAlias.configs.recommended,
  {
    files: ['src/**/*.{ts,tsx}'],
    ignores: ['node_modules/', 'dist/', '**/*.d.ts'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: dirname,
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        console: 'readonly',
        HTMLElement: 'readonly',
      },
    },
    plugins: {
      '@stylistic': stylistic,
      '@typescript-eslint': tseslint,
      import: importPlugin,
      'jsx-a11y': jsxA11y,
      prettier: prettierPlugin,
      'react-hooks': reactHooks,
      'unused-imports': unusedImports,
    },
    settings: {
      'import/resolver': {
        alias: {
          map: [
            ['assets', './src/assets'],
            ['components', './src/components'],
            ['layout', './src/layout'],
            ['pages', './src/pages'],
            ['router', './src/react-router'],
            ['styles', './src/styles'],
            ['ui', './src/ui'],
            ['configuration', './src/configuration'],
            ['lib', './src/lib'],
            ['util', './src/util'],
          ],
          extensions: ['.ts', '.tsx', '.js', '.jsx'],
        },
      },
    },
    rules: {
      ...eslint.configs.recommended.rules,
      ...tseslint.configs.recommended.rules,

      'prettier/prettier': 'error',

      '@typescript-eslint/consistent-type-imports': 'off',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/no-unused-vars': 'off',

      '@dword-design/import-alias/prefer-alias': [
        'error',
        {
          aliasForSubpaths: true,
          alias: {
            assets: './src/assets',
            components: './src/components',
            layout: './src/layout',
            pages: './src/pages',
            router: './src/react-router',
            styles: './src/styles',
            ui: './src/ui',
            configuration: './src/configuration',
            lib: './src/lib',
            util: './src/util',
          },
        },
      ],

      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'error',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_',
        },
      ],

      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error',

      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-is-valid': 'error',
      'jsx-a11y/click-events-have-key-events': 'error',
      'jsx-a11y/no-static-element-interactions': 'error',

      'import/order': [
        'error',
        {
          groups: [
            ['builtin', 'external'],
            ['internal', 'parent', 'sibling', 'index'],
          ],
          pathGroups: [
            { pattern: 'react', group: 'builtin', position: 'before' },
            { pattern: 'axios', group: 'builtin', position: 'after' },
            { pattern: 'configuration/**', group: 'internal', position: 'after' },
            { pattern: 'lib/**', group: 'internal', position: 'after' },
            { pattern: 'assets/**', group: 'internal', position: 'after' },
            { pattern: 'components/**', group: 'internal', position: 'after' },
            { pattern: 'layout/**', group: 'internal', position: 'after' },
            { pattern: 'pages/**', group: 'internal', position: 'after' },
            { pattern: 'router/**', group: 'internal', position: 'after' },
            { pattern: 'styles/**', group: 'internal', position: 'after' },
            { pattern: 'ui/**', group: 'internal', position: 'after' },
            { pattern: 'util/**', group: 'internal', position: 'after' },
          ],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],

      '@stylistic/max-len': [
        'error',
        {
          code: 100,
          tabWidth: 2,
          ignoreUrls: true,
          ignoreStrings: true,
          ignoreTemplateLiterals: true,
          ignoreComments: true,
        },
      ],

      curly: ['error', 'all'],
      eqeqeq: ['error', 'always'],
      'no-console': ['error', { allow: ['warn', 'error'] }],
      'no-restricted-globals': [
        'error',
        { name: 'window', message: 'Use React refs or approved globalThis platform APIs.' },
        { name: 'document', message: 'Use React refs and element-scoped DOM APIs.' },
      ],
      'no-restricted-syntax': [
        'error',
        {
          selector: "MemberExpression[object.name='globalThis'][property.name='window']",
          message: 'globalThis.window is not allowed.',
        },
        {
          selector: "MemberExpression[object.name='globalThis'][property.name='document']",
          message: 'globalThis.document is not allowed.',
        },
      ],
      'no-else-return': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-const': 'error',
    },
  },
];
