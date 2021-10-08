// takes a length and elements to randomly populate the array with
export default (length, ...fillers) =>
  Array.from(
    { length },
    () => fillers[Math.floor(Math.random() * fillers.length)]
  )
