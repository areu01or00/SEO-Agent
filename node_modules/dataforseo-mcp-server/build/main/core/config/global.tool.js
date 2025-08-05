import { z } from 'zod';
export const GlobalToolConfigSchema = z.object({
    fullResponse: z.boolean().default(false),
    debug: z.boolean().default(false)
});
// Parse config from environment variables
export function parseGlobalToolConfig() {
    const fullResponseEnv = process.env.DATAFORSEO_FULL_RESPONSE;
    const debugEnv = process.env.DEBUG;
    const config = {
        fullResponse: fullResponseEnv === 'true',
        debug: debugEnv === 'true'
    };
    return GlobalToolConfigSchema.parse(config);
}
// Export default config
export const defaultGlobalToolConfig = parseGlobalToolConfig();
