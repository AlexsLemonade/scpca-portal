export const internationalFormat = (value) => {
  return new Intl.NumberFormat().format(Math.round(value * 10) / 10)
}

export const abbreviateNumbers = (value) => {
  const num = parseInt(value, 10)
  if (num >= 1000 ** 2) {
    return `${internationalFormat(num / 1000000)}M`
  }
  if (num >= 1000) {
    return `${internationalFormat(num / 1000)}k`
  }
  return internationalFormat(num)
}

export default abbreviateNumbers
