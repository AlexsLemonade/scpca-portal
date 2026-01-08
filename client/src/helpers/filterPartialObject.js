export const filterPartialObject = (arrayOfObjects, objectPartial) => {
  return arrayOfObjects.filter((o) => {
    return Object.entries(objectPartial).every(([k, v]) => o[k] === v)
  })
}

export default filterPartialObject
