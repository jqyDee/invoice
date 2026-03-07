import {Gender} from "../api";

export const toGermanGender = (gender: Gender): string => {
    let genderString: string;

    switch (gender) {
        case Gender.FEMALE:
            genderString = "Frau";
            break
        case Gender.MALE:
            genderString = "Mann";
            break
        default:
            genderString = gender;
    }

    return genderString;
}