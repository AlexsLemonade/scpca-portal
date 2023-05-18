module.exports = {
  presets: ['next/babel'],
  plugins: [
    [
      'inline-react-svg',
      {
        svgo: {
          plugins: [
            'cleanupAttrs',
            'removeXMLProcInst',
            'convertTransform',
            'convertPathData',
            'convertStyleToAttrs',
            'removeUselessStrokeAndFill',
            'removeEditorsNSData',
            'removeEmptyContainers',
            'mergePaths',
            'collapseGroups',
            {
              name: 'removeUnknownsAndDefaults',
              params: { attrs: { keepDataAttrs: false } }
            },
            {
              name: 'cleanupIDs',
              params: {
                prefix: {
                  toString() {
                    return `${Math.random().toString(36).substr(2, 9)}`
                  }
                }
              }
            },
            {
              name: 'removeAttrs',
              params: { attrs: '(data-name)' }
            }
          ]
        }
      }
    ],
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
