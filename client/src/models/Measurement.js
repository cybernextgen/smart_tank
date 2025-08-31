export class Measurement {
  static QUALITY_GOOD = 0
  static QUALITY_BAD = 1

  constructor(value = 0, quality = Measurement.QUALITY_GOOD) {
    this.value = value
    this.quality = quality
  }

  isGood() {
    return this.quality === Measurement.QUALITY_GOOD
  }

  isBad() {
    return !this.isGood()
  }
}
