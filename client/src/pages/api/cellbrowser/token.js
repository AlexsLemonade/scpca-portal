import api from "api"
const crypto = require("crypto")

const validateToken = async (token) => {
  const request = await api.tokens.get(token)
  return request.isOk && request.response.is_activated
}

const createClientToken = (token) => {
  const combined = `${token}:${process.env.CLIENT_SECRET}`
  return crypto.createHash("sha256")
    .update(combined)
    .digest("hex")
}

export default async function handler(req, res) {
  if (req.method === "POST") {
    const { 'api-key': token } = req.headers

    // validate API token
    try {
      if (!await validateToken(token)) {
        return res.status(401).json({ error: "Invalid API Token" })
      }
    } catch (error) {
      return res.status(400).json({ error: "Invalid Authorization Header" })
    }

    // create new clientToken
    try {
      const clientToken = createClientToken(token)
      return res.status(200).json({ clientToken })
    } catch {
      return res.status(500).json({ error: "Unexpected Server Error" })
    }
  }
}
