import { writable } from "svelte/store";

export const aller = [
  "난류",
  "우유",
  "메밀",
  "땅콩",
  "대두",
  "밀",
  "고등어",
  "게",
  "새우",
  "돼지고기",
  "복숭아",
  "토마토",
  "아황산류",
  "호두",
  "닭고기",
  "쇠고기",
  "오징어",
  "조개류",
  "잣",
];

export let allergyStoreDefaultValues = {};
aller.forEach((a) => (allergyStoreDefaultValues[a] = false));
export const allergyStore = writable(allergyStoreDefaultValues);

export const emojiEnabledStore = writable(false);
export const switchStateStore = writable(false);
