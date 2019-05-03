// rollup config

import resolve from 'rollup-plugin-node-resolve';
import babel from 'rollup-plugin-babel';
import inject from 'rollup-plugin-inject';

export default {
  input: 'src/js/curtissand.js',
  output: {
    file: 'dist/js/curtissand.js',
    format: 'umd',
    name: 'website'
  },
  external: ['bootstrap', 'jquery'],
  plugins: [
    resolve(),
    babel({
      exclude: 'node_modules/**' // only transpile our source code
    }),
    inject({
      include: '**/*.js',
      exclude: 'node_modules/**',
      jQuery: 'jquery',
    })
  ]
};
