class HandPosition {
    constructor(leftPinky, leftRing, leftMiddle, leftIndex, leftThumb, rightThumb, rightIndex, rightMiddle, rightRing, rightPinky) {
        this.mapping = {
            leftPinky: leftPinky.split(''),
            leftRing: leftRing.split(''),
            leftMiddle: leftMiddle.split(''),
            leftIndex: leftIndex.split(''),
            leftThumb: leftThumb.split(''),
            rightThumb: rightThumb.split(''),
            rightIndex: rightIndex.split(''),
            rightMiddle: rightMiddle.split(''),
            rightRing: rightRing.split(''),
            rightPinky: rightPinky.split(''),
        }
    }
    getFinger(char) {
        return Object.keys(this.mapping).find(key => this.mapping[key].includes(char))
    }
    // colorize(leftPinky, leftRing, leftMiddle, leftIndex, leftThumb, rightThumb, rightIndex, rightMiddle, rightRing, rightPinky) {
    colorize() {
        const fingers = Object.keys(this.mapping)
        fingers.forEach(finger => {
            this.mapping[finger].forEach(key => {
                $(`.kb-key[data-key="${key}"]`).addClass(finger)
                console.log(key)
            })
        })
    }
}
