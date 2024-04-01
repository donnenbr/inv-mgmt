// just an example of including an "external" js file in the app.
// taken from https://www.geeksforgeeks.org/how-to-include-a-javascript-file-in-angular-and-call-a-function-from-that-script/
export function print() {
    console.log('Hello there big fat World!!')
 }


 export class MyClass {
    firstName = "";
    lastName = "";
    age = 0;

    constructor(fname, lname, age) {
        this.firstName = fname;
        this.lastName = lname;
        this.age = age;
    }

    printMe() {
        return this.firstName + " " + this.lastName + ", " + this.age;
    }
 }