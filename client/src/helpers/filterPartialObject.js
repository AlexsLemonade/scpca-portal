export const filterPartialObject = (arrayOfObjects, objectPartial) =>
  arrayOfObjects.filter((o) =>
    Object.entries(objectPartial).every(([k, v]) => o[k] === v)
  )

export default filterPartialObject
