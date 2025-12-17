module.exports = {
  presets: ['next'],
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
                prefix: 'badge-'
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
