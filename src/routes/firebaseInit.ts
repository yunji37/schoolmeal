import { getAuth } from "firebase/auth";
import { initializeApp, getApps } from "firebase/app";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
    apiKey: "AIzaSyApch2Rd5aBdBvIn4ExkLKhsopuR-L1ApE",
    authDomain: "user-7d8a2.firebaseapp.com",
    projectId: "user-7d8a2",
    storageBucket: "user-7d8a2.appspot.com",
    messagingSenderId: "929689585521",
    appId: "1:929689585521:web:b6fc14732707ee066c98d0",
    measurementId: "G-7DTYH1Y46T",
    databaseURL:
        "https://user-7d8a2-default-rtdb.asia-southeast1.firebasedatabase.app/",
};

let app;
if (!getApps().length) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApps()[0];
}

export const auth = getAuth(app);
export const db = getDatabase(app);
