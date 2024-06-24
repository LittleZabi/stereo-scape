<script lang="ts">
	import { slide } from 'svelte/transition';
	// @ts-ignore
	import { updateSettings } from '$lib/store';
	import { editMediaContext, updateMediaContext } from '../lib/store';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import axios from 'axios';

	console.log($editMediaContext);
	let loading = false;
	const handleVidGen = async () => {
		const form = new FormData();
		form.append('media', $editMediaContext.media);
		form.append('user', $editMediaContext.user);
		form.append('_id', $editMediaContext._id);
		loading = true;
		await axios
			.post(`${PUBLIC_BACKEND_URL}/generate-video`, form)
			.then((res: any) => {
				res = res.data;
				loading = false;
				if (res.success) {
					updateMediaContext({ ...$editMediaContext, video: res.video });
				} else {
					console.error(res.message);
				}
			})
			.catch((err) => {
				console.error(err);
				loading = false;
			});
	};
</script>

<div class="modal" transition:slide>
	<div class="head">
		<h3>Edit pre-trained model of @{$editMediaContext.username}</h3>
		<button class="xuw" on:click={() => updateMediaContext(false)}>&times;</button>
	</div>
	<div class="container" id="setting_form">
		<p>Media identification ({$editMediaContext.media})</p>
		<br />
		<p>360 video</p>
		{#if $editMediaContext.video}
			<video controls src={PUBLIC_BACKEND_URL + $editMediaContext.video}>
				<track kind="captions" />
			</video>
		{:else}
			<button class="button" on:click={handleVidGen}>Click to generate 360 video</button>
		{/if}
		{#if loading}
			loading...
		{/if}
	</div>
</div>

<style lang="scss">
	.button {
		padding: 10px 20px;
		margin-top: 10px;
		font-size: 16px;
		background: rgb(11, 36, 120);
		color: white;
		border: 2px solid rgb(10, 78, 118);
		border-radius: 28px;
	}
	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.container {
		margin-top: 30px;
	}
	.modal {
		position: fixed;
		z-index: 30;
		background: rgba(16, 16, 43, 0.704);
		left: 0;
		right: 0;
		backdrop-filter: blur(18px);
		top: 0;
		bottom: 0;
		max-width: 980px;
		max-height: 68%;
		margin: auto;
		border-radius: 8px;
		padding: 25px;
	}
</style>
