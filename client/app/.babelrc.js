module.exports = {
  presets: ['next'],
  plugins: [
    [
      'styled-components',
      {
        ssr: true,
        displayName: true,
        preprocess: false,
        minify: true,
        transpileTemplateLiterals: true,
        pure: true
      }
    ]
  ]
}
