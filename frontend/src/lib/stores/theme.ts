import { writable } from 'svelte/store';

export const theme = writable<boolean>(false); // false = light, true = dark
