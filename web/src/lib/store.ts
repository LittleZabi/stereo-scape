import { writable } from 'svelte/store';

export const fluidCb = writable((rain=1) => {});

export const updateFluidCb = (cb) => {
    fluidCb.set(cb)
};

export const viewPageIndex = writable(0)
export const updatePageIndex = (index) => viewPageIndex.update(() => index)
