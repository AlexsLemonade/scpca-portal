/*
@name getHash
@description returns the hash property (a fragment indentifier) of the location object
*/
export const getHash = () =>
  typeof window !== 'undefined' ? window.location.hash : undefined

export default getHash
