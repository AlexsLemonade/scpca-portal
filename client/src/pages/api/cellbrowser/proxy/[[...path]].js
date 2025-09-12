import { createProxyMiddleware } from 'http-proxy-middleware'
const crypto = require("crypto")


const validateTokens = (clientToken, token) => {
  const combined = `${token}:${process.env.CLIENT_SECRET}`
  const expectedToken = crypto.createHash("sha256")
    .update(combined)
    .digest("hex")

  return clientToken === expectedToken
}

const cellbrowserS3Proxy = createProxyMiddleware({
  target: process.env.CELLBROWSER_STATIC_HOST,
  changeOrigin: true,
  pathRewrite: {
    '^/api/cellbrowser/proxy': '',
  },
  on: {
    proxyReq: (proxyReq, req, _res) => {
      const isOpen = !req.url.startsWith("/SCPCP")
      const { authorization: clientToken, 'api-key': token } = req.headers

      if (isOpen || validateTokens(clientToken, token)) {
        console.log(req.url)
        proxyReq.setHeader('Referer', process.env.CELLBROWSER_SECRET)
      } else {
        console.error(req.url)
      }
    }
  },
})

export default function handler(req, res) {
  cellbrowserS3Proxy(req, res)
}

export const config = {
  api: {
    bodyParser: false,
    externalResolver: true,
  },
}
