export class Message {
  constructor(statusCode, text) {
    this.statusCode = statusCode
    this.text = text
    this.datetime = new Date()
  }
}
