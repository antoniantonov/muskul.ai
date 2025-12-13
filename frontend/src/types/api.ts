import { z } from 'zod';

// Activity types
export const ActivityTypeSchema = z.enum([
  'running',
  'cycling',
  'swimming',
  'walking',
  'hiking',
  'gym',
  'other',
]);

export type ActivityType = z.infer<typeof ActivityTypeSchema>;

// Activity schema
export const ActivitySchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  activity_type: ActivityTypeSchema,
  start_time: z.string().datetime(),
  end_time: z.string().datetime().optional(),
  duration_seconds: z.number().int().positive().optional(),
  distance_meters: z.number().positive().optional(),
  calories: z.number().positive().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type Activity = z.infer<typeof ActivitySchema>;

// Provider schema
export const ProviderSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  provider_type: z.string(),
  connected: z.boolean(),
  last_sync: z.string().datetime().optional(),
});

export type Provider = z.infer<typeof ProviderSchema>;

// API response schemas
export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number().int().nonnegative(),
    page: z.number().int().positive(),
    page_size: z.number().int().positive(),
  });

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

// Error response schema
export const ErrorResponseSchema = z.object({
  error: z.string(),
  message: z.string(),
  details: z.record(z.unknown()).optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
