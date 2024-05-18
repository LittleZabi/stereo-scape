<script lang="ts">
	import { userContext } from '../lib/store';
	// @ts-ignore
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Icon from '@iconify/svelte';
	import { onMount } from 'svelte';
	import { lazyLoad } from '../lib/globals';

	onMount(() => {
		const lazyLoadList = document.querySelectorAll('.lazy-load');
		lazyLoadList.forEach((element: HTMLImageElement | HTMLVideoElement) => {
			let src = element.getAttribute('data-src');
			lazyLoad(element, src);
		});
	});
</script>

<div class="profile">
	<div class="left">
		<div class="pic">
			<img src={$userContext.avatar} alt={$userContext.username} />
		</div>
		<span class="username"
			>@{$userContext.username}
			<br />
			{$userContext.passion != '' ? $userContext.passion : ''}
		</span>
		<span class="email">{$userContext.email}</span>
		<button>
			Logout <Icon icon="solar:logout-2-broken" />
		</button>
	</div>
	<div class="right">
		<h3>My gallery</h3>
		<div class="">
			<button class="tim">
				<span>12 May 2024 </span>
				<Icon icon="oui:arrow-down" />
			</button>
			<button class="tim">
				<span>30 January 2024</span>
				<Icon icon="oui:arrow-down" />
			</button>
			<div class="rows" id="scrollar">
				{#each Array(10).fill(0) as _}
					<div class="gal">
						<video controls class="lazy-load" data-src={PUBLIC_BACKEND_URL + '/videos/trex.mp4'}>
							<track kind="captions" />
						</video>
						<div class="galx">
							<span class="t"
								><li>Trex 360 view full viewo f the askdflaskfa sdlfkjasdlf gozida</li></span
							>
							<a href="/datasetr">
								<Icon icon="ph:images-fill" />
								View images
							</a>
							<a href="/npz">
								<Icon icon="majesticons:data-line" />
								Download dataset file
							</a>
							<a href="/model">
								<Icon icon="carbon:machine-learning-model" />
								Download trained model</a
							>
							<span class="xz">Created on 23 june 2019</span>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>

<style lang="scss">
	.rows {
		display: flex;
		max-width: 72vw;
		flex-wrap: nowrap;
		flex-direction: row;
		justify-content: flex-start;
		overflow-x: scroll;
	}
	.tim {
		width: max-content;
		min-width: 150px;
		padding: 0 0px 0 10px;
		margin-top: 10px;
		margin-bottom: 10px;
		color: rgb(170, 170, 170);
		font-size: 14px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.051);
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: none;
		border: none;
		transition: 400ms;
		cursor: pointer;
		&:hover,
		&.active {
			color: white;
		}
	}
	:global(.galx a svg) {
		margin-right: 5px;
		font-size: 18px;
	}
	.xz {
		font-size: 12px;
		margin-top: 25px;
		color: rgba(255, 255, 255, 0.596);
	}
	.galx {
		display: flex;
		flex-direction: column;
		margin-left: 10px;
		width: 200px;
		& a {
			margin-top: 8px;
			font-size: 14px;
			display: flex;
			align-items: center;
			transition: 300ms;
			&:hover {
				color: rgb(255, 67, 154);
			}
		}
		& .t {
			margin-bottom: 20px;
			max-width: 200px;
		}
		& span {
			display: block;
		}
	}
	.gal {
		margin: 10px;
		display: flex;
		align-items: start;
		justify-content: center;
		flex-direction: row;
		& video {
			width: 200px;
			height: 180px;
			object-fit: cover;
			border-radius: 13px;
		}
	}
	.right {
		border-left: 1px solid rgba(255, 255, 255, 0.076);
		min-width: 300px;
		min-height: 300px;
		padding-left: 15px;
		& h3 {
			font-size: 16px;
		}
	}
	:global(.profile .left button svg) {
		margin-left: 10px;
		font-size: 20px;
		display: block;
		background-color: blue($color: #000000);
	}
	.left {
		display: flex;
		align-items: center;
		justify-content: start;
		flex-direction: column;
		margin-right: 20px;
		& button {
			padding: 8px 20px;
			margin-top: 20px;
			background: rgba(0, 0, 0, 0.181);
			color: white;
			border: 1px solid rgba(255, 255, 255, 0.089);
			display: flex;
			justify-content: center;
			align-items: center;
			cursor: pointer;
			transition: 400ms;
			&:hover {
				background: black;
			}
		}

		& span.email {
			margin-top: 3px;
			margin-bottom: 3px;
			color: rgb(182, 182, 182);
		}
		& span.username {
			margin-top: 8px;
			color: rgb(229, 229, 229);
			font-size: 14px;
			text-align: center;
		}
		& .pic {
			width: 80px;
			height: 80px;
			border-radius: 50%;
			border: 2px solid rgba(255, 255, 255, 0.285);
			overflow: hidden;
		}
		& img {
			width: 100%;
			height: 100%;
			object-fit: cover;
		}
	}
	.profile {
		display: flex;
	}
</style>
