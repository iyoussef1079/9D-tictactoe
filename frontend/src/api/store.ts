// src/api/store.ts
import { writable } from 'svelte/store';

export const isWebSocketConnected = writable(false);
