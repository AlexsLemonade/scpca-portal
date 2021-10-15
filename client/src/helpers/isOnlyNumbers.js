// regex test to check that a string is only numbers

export const isOnlyNumbers = (input) => {
  return /^\d+$/.test(input)
}

export default isOnlyNumbers
