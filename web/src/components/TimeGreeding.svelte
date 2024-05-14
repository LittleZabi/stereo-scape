<script lang="ts">
	import { life } from '../lib/globals';
	const dayPortion = life(Date()).dayPortion();
</script>

<h1 class="main-day-portion">
	{dayPortion[0]}
	<span>
		Today is {life(Date()).format('D Mm, YYYY')}
		{dayPortion[1]}.
	</span>
</h1>

<style lang="scss">
	.main-day-portion {
		text-align: center;
		font-weight: 500;
		font-size: 42px;
		letter-spacing: 1px;
		& span {
			text-transform: unset;
			letter-spacing: 0;
			font-size: 14px;
			font-weight: 500;
			display: block;
		}
		margin-bottom: 22px;
	}
</style>
