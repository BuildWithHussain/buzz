// Currency formatting utilities using JavaScript Intl API

export function formatCurrency(
	amount: number | string,
	currencyCode: string = "INR",
	locale: string = "en-US"
): string {
	const amountNum = typeof amount === "string" ? parseFloat(amount) : amount;
	try {
		return new Intl.NumberFormat(locale, {
			style: "currency",
			currency: currencyCode,
		}).format(amountNum);
	} catch (error) {
		// Fallback if currency code is invalid or not supported
		console.warn(
			`Invalid currency code: ${currencyCode}. Falling back to default formatting.`
		);
		return new Intl.NumberFormat(locale, {
			style: "currency",
			currency: "INR",
		}).format(amountNum);
	}
}

export function formatPrice(
	price: number | string,
	currencyCode: string = "INR",
	locale: string = "en-US"
): string {
	return formatCurrency(price, currencyCode, locale);
}

export function formatPriceOrFree(
	price: number | string,
	currencyCode: string = "INR",
	locale: string = "en-US"
): string {
	if (price === 0 || price === "0") {
		// @ts-ignore: __ is global
		return __("Free");
	}
	return formatPrice(price, currencyCode, locale);
}

export function getCurrencySymbol(currencyCode: string, locale: string = "en-US"): string {
	try {
		const formatter = new Intl.NumberFormat(locale, {
			style: "currency",
			currency: currencyCode,
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		});

		// Format a small number and extract just the symbol
		const formatted = formatter.format(0);
		return formatted.replace(/[\d\s,]/g, "").trim();
	} catch (error) {
		console.warn(`Invalid currency code: ${currencyCode}`);
		return currencyCode;
	}
}
