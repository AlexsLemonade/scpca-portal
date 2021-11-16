// this makes the assumption any local link will be given as
// a relative or absolute path with no protocol
export const isExternalPath = (path = '') => {
  return path && path.startsWith('http')
}

export default isExternalPath
