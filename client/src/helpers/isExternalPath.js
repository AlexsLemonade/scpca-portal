// this makes the assumption any local link will be given as
// a relative or absolute path with no protocol
export default (path = '') => {
  return path && path.startsWith('http')
}
