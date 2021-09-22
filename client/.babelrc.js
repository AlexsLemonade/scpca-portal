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
              name: 'cleanupIDs',
              params: {
                prefix: {
                  toString() {
                    return `${Math.random().toString(36).substr(2, 9)}`
                  }
                }
              }
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
        preprocess: false
      }
    ]
  ]
}
