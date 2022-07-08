export const countMultiplexedSamples = (arr) => {
  // TODO: ask about multiplexed sample count in API
  let counter = 0
  arr.forEach((c) => {
    if (c.additional_metadata.multiplexed_with.length > 0) {
      counter += 1
    }
  }, 0)

  return counter
}

export default countMultiplexedSamples
