import { BaseTool } from '../../../base.tool.js';
export class GoogleTrendsCategoriesTool extends BaseTool {
    constructor(dataForSEOClient) {
        super(dataForSEOClient);
    }
    getName() {
        return 'keywords_data_google_trends_categories';
    }
    getDescription() {
        return 'This endpoint will provide you list of Google Trends Categories';
    }
    getParams() {
        return {};
    }
    async handle(params) {
        try {
            const response = await this.dataForSEOClient.makeRequest('/v3/keywords_data/google_trends/categories/live', 'GET');
            return this.validateAndFormatResponse(response);
        }
        catch (error) {
            return this.formatErrorResponse(error);
        }
    }
}
