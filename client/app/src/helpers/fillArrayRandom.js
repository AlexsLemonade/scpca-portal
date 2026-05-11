// takes a length and elements to randomly populate the array with
export const fillArrayRandom = (length, ...fillers) =>
  Array.from(
    { length },
    () => fillers[Math.floor(Math.random() * fillers.length)]
  )

export default fillArrayRandom
