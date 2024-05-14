<script>
	import Footer from '../components/Footer.svelte';
	import Header from '../components/Header.svelte';
	import ThreeScene from '../threeScenes/threeScene.svelte';
	import '../styles/main.scss';
	import { onMount } from 'svelte';
	import { Cookies } from '../lib/globals';
	import { viewPageIndex, updatePageIndex } from '../lib/store';

	let fluidLights = false;
	let buttonIndex = 0
	$:$viewPageIndex, buttonIndex = $viewPageIndex 
	onMount(() => {
		const f = JSON.parse(Cookies.get('fluid_lights'));
		if (f === null) fluidLights = true;
		else fluidLights = f;
	});
	const toggleFluid = () => {
		fluidLights = !fluidLights;
		Cookies.set('fluid_lights', fluidLights);
	};
	const handlePage = (i) => {
		updatePageIndex(i)
	}
</script>

{#if fluidLights}
	<ThreeScene />
{/if}
<div class="wrapper" id="boundary">
	<div class="boundary">
		<Header fluidToggle={toggleFluid} fluid={fluidLights} />
		<main>
			<slot />
			<div class="left-button-list">
				{#each Array(4).fill(0) as _,i }
					<button on:click={() => handlePage(i)} class={buttonIndex === i ? 'active' : ''}>
					</button>
				{/each}
			</div>
		</main>
		<Footer />
	</div>
</div>

<style>
	.left-button-list {
		display: flex;
		position: fixed;
		right: 20px;
		align-items: center;
		justify-content: center;
		top: 0;
		bottom: 0;
		flex-direction: column;
		& button {
			border-radius: 50%;
			width: 16px;
			height: 16px;
			border: 2px solid #ffffff3b;
			text-align: center;
			padding: 0;
			cursor: pointer;
			background: #fdfdfd4f;
			margin: 3px 0;
			transition: 300ms;
			&:hover{
				background:#ffffffc8; 
			}
			&.active{
				background:#ffffffc8; 

			}
		}
	}
	.boundary {
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}
</style>
