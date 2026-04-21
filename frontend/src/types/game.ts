export interface GameData {
    game_id?: string;
    name: string;
    description: string;
    recommendation_percent: number;
    summary_positive: number;
    summary_negative: number;
    from_platform: number;
    img_url: string;
}

export interface GameEmptyData {
    message?: string;
}

export type GameDataResponse = GameData[] | GameEmptyData | null | undefined;