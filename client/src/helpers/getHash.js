// Returns the hash property (a fragment indentifier) of the location object
export default () =>
  typeof window !== 'undefined' ? window.location.hash : undefined
