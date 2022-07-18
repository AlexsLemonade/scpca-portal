/*
@name hasRecommendedResource
@description returns true if a type matches one of types, otherwise false
@param {string} type - a computed file type
*/
export const hasRecommendedResource = (type) => {
  const types = ['SAMPLE_MULTIPLEXED_ZIP']

  return types.includes(type)
}

export default hasRecommendedResource
