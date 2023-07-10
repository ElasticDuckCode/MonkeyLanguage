let reduce = fn(arr, init, f) {
	let iter = fn(arr, result) {
		if (len(arr) == 0) {
			return result;
		}
		else {
			iter(rest(arr), f(result, first(arr)));
		}
	}
	iter(arr, init);
};

let sum = fn(arr) {
	reduce(arr, 0, fn(init, el) { init + el });
};

let a = [1, 2, 3, 4];
sum(a)
