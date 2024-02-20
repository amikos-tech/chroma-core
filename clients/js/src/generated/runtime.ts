import 'isomorphic-fetch';
/* eslint-disable */
// tslint:disable
/**
 * FastAPI
 * 
 *
 * OpenAPI spec version: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator+.
 * https://github.com/karlvr/openapi-generator-plus
 * Do not edit the class manually.
 */

export const defaultFetch = fetch;
import { Configuration } from "./configuration";

export const BASE_PATH = "";

/**
 *
 * @export
 */
export const COLLECTION_FORMATS = {
	csv: ",",
	ssv: " ",
	tsv: "\t",
	pipes: "|",
};

/**
 *
 * @export
 * @type FetchAPI
 */
export type FetchAPI = typeof defaultFetch;

/**
 *  
 * @export
 * @interface FetchArgs
 */
export interface FetchArgs {
	url: string;
	options: RequestInit;
}

/**
 * 
 * @export
 * @class BaseAPI
 */
export class BaseAPI {
	protected configuration?: Configuration;

	constructor(configuration?: Configuration, protected basePath: string = BASE_PATH, protected fetch: FetchAPI = defaultFetch) {
		if (configuration) {
			this.configuration = configuration;
			this.basePath = configuration.basePath || this.basePath;
		}
	}
};

/**
 * 
 * @export
 * @class RequiredError
 * @extends {Error}
 */
export class RequiredError extends Error {
	constructor(public field: string, msg?: string) {
		super(msg);
		Object.setPrototypeOf(this, RequiredError.prototype);
		this.name = "RequiredError";
	}
}
