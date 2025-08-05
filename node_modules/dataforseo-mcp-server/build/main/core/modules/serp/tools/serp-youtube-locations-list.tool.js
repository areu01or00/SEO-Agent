import { z } from 'zod';
import { BaseTool } from '../../base.tool.js';
export class SerpYoutubeLocationsListTool extends BaseTool {
    constructor(dataForSEOClient) {
        super(dataForSEOClient);
    }
    getName() {
        return 'serp_youtube_locations';
    }
    getDescription() {
        return 'Utility tool to get list of available locations for: serp_youtube_organic_live_advanced, serp_youtube_video_info_live_advanced, serp_youtube_video_comments_live_advanced, serp_youtube_video_subtitles_live_advanced';
    }
    supportOnlyFullResponse() {
        return true;
    }
    getParams() {
        return {
            country_code: z.string().default('US').describe("country code (e.g., 'US')"),
        };
    }
    async handle(params) {
        try {
            console.error(JSON.stringify(params, null, 2));
            const response = await this.dataForSEOClient.makeRequest(`/v3/serp/youtube/locations/${params.country_code}`, 'GET', null, true);
            this.validateResponseFull(response);
            return this.formatResponse(response.tasks[0].result.map(x => x.location_name));
        }
        catch (error) {
            return this.formatErrorResponse(error);
        }
    }
}
