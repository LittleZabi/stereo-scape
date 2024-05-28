import { writable } from 'svelte/store';

export const fluidCb = writable((rain=1) => {});

export const updateFluidCb = (cb) => {
    fluidCb.set(cb)
};
export const imagesContext:any = writable([])
export const updateImages = (images:any) => imagesContext.update(() => images) 

export const userContext:any = writable(false)
export const userContextUpdate:(user: {[key:string]:any} | boolean) => any = (user) => {
    userContext.update(() => user)
}

export const viewPageIndex = writable([0, 0])
export const updatePageIndex = (index:[number, number]) => viewPageIndex.update(() => index)

export const SettingsContext = writable({
    modal_depth: 8,
    modal_width: 256,
    n_samples: 64,
    image_width: 100,
    image_height: 100,
    n_iterations: 250,
    isOpened: false
});
export const updateSettings = (setting:any) => SettingsContext.update((state:{[key:string]: any}) => ({...state, ...setting}))
