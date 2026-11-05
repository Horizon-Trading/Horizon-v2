export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      executions: {
        Row: {
          cumulative_quantity: number
          id: number
          observed_at: string
          order_id: string
          price: number
          quantity: number
          source: string
        }
        Insert: {
          cumulative_quantity: number
          id?: never
          observed_at?: string
          order_id: string
          price: number
          quantity: number
          source?: string
        }
        Update: {
          cumulative_quantity?: number
          id?: never
          observed_at?: string
          order_id?: string
          price?: number
          quantity?: number
          source?: string
        }
        Relationships: [
          {
            foreignKeyName: "executions_order_id_fkey"
            columns: ["order_id"]
            isOneToOne: false
            referencedRelation: "orders"
            referencedColumns: ["id"]
          },
        ]
      }
      market_snapshots: {
        Row: {
          captured_at: string
          feature_data: Json
          float_shares: number | null
          id: string
          market_adjusted_return: number | null
          market_cap: number | null
          news_event_id: string | null
          price: number
          price_change: number | null
          price_observed_at: string | null
          relative_volume: number | null
          ticker: string
          volatility: number | null
          volume: number | null
        }
        Insert: {
          captured_at?: string
          feature_data?: Json
          float_shares?: number | null
          id?: string
          market_adjusted_return?: number | null
          market_cap?: number | null
          news_event_id?: string | null
          price: number
          price_change?: number | null
          price_observed_at?: string | null
          relative_volume?: number | null
          ticker: string
          volatility?: number | null
          volume?: number | null
        }
        Update: {
          captured_at?: string
          feature_data?: Json
          float_shares?: number | null
          id?: string
          market_adjusted_return?: number | null
          market_cap?: number | null
          news_event_id?: string | null
          price?: number
          price_change?: number | null
          price_observed_at?: string | null
          relative_volume?: number | null
          ticker?: string
          volatility?: number | null
          volume?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "market_snapshots_news_event_id_fkey"
            columns: ["news_event_id"]
            isOneToOne: true
            referencedRelation: "news_events"
            referencedColumns: ["id"]
          },
        ]
      }
      news_events: {
        Row: {
          author: string | null
          created_at: string
          event_type: string | null
          id: string
          next_snapshot_attempt_at: string
          provider: string
          provider_event_id: string
          published_at: string
          raw_data: Json | null
          received_at: string
          snapshot_attempts: number
          snapshot_error: string | null
          source: string | null
          summary: string | null
          ticker: string
          title: string
          url: string
        }
        Insert: {
          author?: string | null
          created_at?: string
          event_type?: string | null
          id?: string
          next_snapshot_attempt_at?: string
          provider: string
          provider_event_id: string
          published_at: string
          raw_data?: Json | null
          received_at?: string
          snapshot_attempts?: number
          snapshot_error?: string | null
          source?: string | null
          summary?: string | null
          ticker: string
          title: string
          url: string
        }
        Update: {
          author?: string | null
          created_at?: string
          event_type?: string | null
          id?: string
          next_snapshot_attempt_at?: string
          provider?: string
          provider_event_id?: string
          published_at?: string
          raw_data?: Json | null
          received_at?: string
          snapshot_attempts?: number
          snapshot_error?: string | null
          source?: string | null
          summary?: string | null
          ticker?: string
          title?: string
          url?: string
        }
        Relationships: []
      }
      orders: {
        Row: {
          broker_order_id: string | null
          broker_updated_at: string | null
          client_order_id: string
          created_at: string
          entry_order_id: string | null
          error: string | null
          exposure_closed: boolean
          filled_avg_price: number | null
          filled_quantity: number
          id: string
          limit_price: number | null
          purpose: string
          quantity: number
          reason: string
          side: string
          signal_id: string | null
          status: string
          submission_attempts: number
          ticker: string
          updated_at: string
        }
        Insert: {
          broker_order_id?: string | null
          broker_updated_at?: string | null
          client_order_id: string
          created_at?: string
          entry_order_id?: string | null
          error?: string | null
          exposure_closed?: boolean
          filled_avg_price?: number | null
          filled_quantity?: number
          id?: string
          limit_price?: number | null
          purpose: string
          quantity: number
          reason: string
          side: string
          signal_id?: string | null
          status?: string
          submission_attempts?: number
          ticker: string
          updated_at?: string
        }
        Update: {
          broker_order_id?: string | null
          broker_updated_at?: string | null
          client_order_id?: string
          created_at?: string
          entry_order_id?: string | null
          error?: string | null
          exposure_closed?: boolean
          filled_avg_price?: number | null
          filled_quantity?: number
          id?: string
          limit_price?: number | null
          purpose?: string
          quantity?: number
          reason?: string
          side?: string
          signal_id?: string | null
          status?: string
          submission_attempts?: number
          ticker?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "orders_entry_order_id_fkey"
            columns: ["entry_order_id"]
            isOneToOne: false
            referencedRelation: "orders"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "orders_signal_id_fkey"
            columns: ["signal_id"]
            isOneToOne: false
            referencedRelation: "signals"
            referencedColumns: ["id"]
          },
        ]
      }
      positions: {
        Row: {
          avg_entry_price: number
          closed_at: string | null
          entry_order_id: string
          opened_at: string
          quantity: number
          realized_pnl: number
          ticker: string
          updated_at: string
        }
        Insert: {
          avg_entry_price: number
          closed_at?: string | null
          entry_order_id: string
          opened_at: string
          quantity: number
          realized_pnl?: number
          ticker: string
          updated_at?: string
        }
        Update: {
          avg_entry_price?: number
          closed_at?: string | null
          entry_order_id?: string
          opened_at?: string
          quantity?: number
          realized_pnl?: number
          ticker?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "positions_entry_order_id_fkey"
            columns: ["entry_order_id"]
            isOneToOne: true
            referencedRelation: "orders"
            referencedColumns: ["id"]
          },
        ]
      }
      signal_history: {
        Row: {
          data: Json
          id: number
          recorded_at: string
          signal_id: string
        }
        Insert: {
          data: Json
          id?: never
          recorded_at?: string
          signal_id: string
        }
        Update: {
          data?: Json
          id?: never
          recorded_at?: string
          signal_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "signal_history_signal_id_fkey"
            columns: ["signal_id"]
            isOneToOne: false
            referencedRelation: "signals"
            referencedColumns: ["id"]
          },
        ]
      }
      signals: {
        Row: {
          analysis: Json
          confidence: number | null
          created_at: string
          expected_return: number | null
          id: string
          market_snapshot_id: string | null
          model_version: string
          news_event_id: string | null
          probability_profit: number | null
          score: number | null
          ticker: string
          updated_at: string
        }
        Insert: {
          analysis?: Json
          confidence?: number | null
          created_at?: string
          expected_return?: number | null
          id?: string
          market_snapshot_id?: string | null
          model_version?: string
          news_event_id?: string | null
          probability_profit?: number | null
          score?: number | null
          ticker: string
          updated_at?: string
        }
        Update: {
          analysis?: Json
          confidence?: number | null
          created_at?: string
          expected_return?: number | null
          id?: string
          market_snapshot_id?: string | null
          model_version?: string
          news_event_id?: string | null
          probability_profit?: number | null
          score?: number | null
          ticker?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "signals_market_snapshot_id_fkey"
            columns: ["market_snapshot_id"]
            isOneToOne: false
            referencedRelation: "market_snapshots"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "signals_matching_snapshot_fk"
            columns: ["market_snapshot_id", "news_event_id", "ticker"]
            isOneToOne: false
            referencedRelation: "market_snapshots"
            referencedColumns: ["id", "news_event_id", "ticker"]
          },
          {
            foreignKeyName: "signals_news_event_id_fkey"
            columns: ["news_event_id"]
            isOneToOne: true
            referencedRelation: "news_events"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      apply_paper_order_state: {
        Args: {
          average_price: number
          broker_id: string
          broker_status: string
          broker_timestamp: string
          cumulative_quantity: number
          local_order_id: string
        }
        Returns: undefined
      }
      pending_signal_events: {
        Args: { batch_size?: number }
        Returns: {
          author: string | null
          created_at: string
          event_type: string | null
          id: string
          next_snapshot_attempt_at: string
          provider: string
          provider_event_id: string
          published_at: string
          raw_data: Json | null
          received_at: string
          snapshot_attempts: number
          snapshot_error: string | null
          source: string | null
          summary: string | null
          ticker: string
          title: string
          url: string
        }[]
        SetofOptions: {
          from: "*"
          to: "news_events"
          isOneToOne: false
          isSetofReturn: true
        }
      }
      pending_snapshot_events: {
        Args: { batch_size?: number }
        Returns: {
          author: string | null
          created_at: string
          event_type: string | null
          id: string
          next_snapshot_attempt_at: string
          provider: string
          provider_event_id: string
          published_at: string
          raw_data: Json | null
          received_at: string
          snapshot_attempts: number
          snapshot_error: string | null
          source: string | null
          summary: string | null
          ticker: string
          title: string
          url: string
        }[]
        SetofOptions: {
          from: "*"
          to: "news_events"
          isOneToOne: false
          isSetofReturn: true
        }
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const

