import { z } from 'zod';
import { BaseTool } from '../../base.tool.js';
export class SerpOrganicLocationsListTool extends BaseTool {
    constructor(dataForSEOClient) {
        super(dataForSEOClient);
    }
    getName() {
        return 'serp_locations';
    }
    getDescription() {
        return 'Utility tool for serp_organic_live_advanced to get list of availible locations';
    }
    supportOnlyFullResponse() {
        return true;
    }
    getParams() {
        return {
            search_engine: z.string().default('google').describe("search engine name, one of: google, yahoo, bing."),
            country_code: z.string().default('US').describe("country code (e.g., 'US')"),
        };
    }
    async handle(params) {
        try {
            console.error(JSON.stringify(params, null, 2));
            const response = await this.dataForSEOClient.makeRequest(`/v3/serp/${params.search_engine}/locations/${params.country_code}`, 'GET', null, true);
            this.validateResponseFull(response);
            return this.formatResponse(response.tasks[0].result.map(x => x.location_name));
        }
        catch (error) {
            return this.formatErrorResponse(error);
        }
    }
}
