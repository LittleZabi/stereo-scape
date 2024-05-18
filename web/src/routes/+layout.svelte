<script>
	import Footer from '../components/Footer.svelte';
	import Header from '../components/Header.svelte';
	import ThreeScene from '../threeScenes/threeScene.svelte';
	import '../styles/main.scss';
	import { onMount } from 'svelte';
	import { Cookies } from '../lib/globals';
	import { viewPageIndex, updatePageIndex, userContextUpdate } from '../lib/store';

	let fluidLights = false;
	let buttonIndex = 0;
	$: $viewPageIndex, (buttonIndex = $viewPageIndex);

	let labels = [
		'Stereo Scape',
		'Welcome!',
		'What is NeRF?',
		'Upload your images',
		'Gallery',
		'Profile'
	];
	onMount(() => {
		const f = JSON.parse(Cookies.get('fluid_lights'));
		if (f === null) fluidLights = true;
		else fluidLights = f;

		let user = Cookies.get('user');
		if (user) {
			user = JSON.parse(user);
			userContextUpdate(user);
		}
	});
	const toggleFluid = () => {
		fluidLights = !fluidLights;
		Cookies.set('fluid_lights', fluidLights);
	};
	const handlePage = (i) => {
		updatePageIndex(i);
	};
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
				{#each labels as label, i}
					<button
						on:click={() => handlePage(i)}
						class={buttonIndex === i ? 'tag-uper active' : 'tag-uper'}
					>
						<span class="tag-label">{label}</span>
					</button>
				{/each}
			</div>
		</main>
		<Footer />
	</div>
</div>

<style>
	.tag-uper {
		position: relative;
		&:hover {
			& .tag-label {
				visibility: visible;
				opacity: 1;
			}
		}
	}
	.tag-label {
		background: #0f202f;
		border: 1px solid #ffffff17;
		position: relative;
		position: absolute;
		right: 24px;
		top: -5px;
		width: max-content;
		display: block;
		padding: 3px 7px;
		border-radius: 2px;
		padding-right: 9px;
		color: rgba(255, 255, 255, 0.843);
		font-size: 12px;
		visibility: hidden;
		opacity: 0;
		transition: 300ms;
		&:after {
			content: '';
			width: 7px;
			height: 7px;
			background: #0f202f;
			border-top: 1px solid #ffffff17;
			border-right: 1px solid #ffffff17;
			position: absolute;
			right: -5px;
			transform: rotate(45deg);
			top: 6px;
			bottom: 0;
		}
	}
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
			&:hover {
				background: #ffffffc8;
			}
			&.active {
				background: #ffffffc8;
			}
		}
	}
	.boundary {
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}
</style>
