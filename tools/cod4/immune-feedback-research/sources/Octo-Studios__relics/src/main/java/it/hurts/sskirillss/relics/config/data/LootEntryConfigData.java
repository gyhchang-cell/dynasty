package it.hurts.sskirillss.relics.config.data;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LootEntryConfigData {
    private List<String> dimensions;
    private List<String> biomes;
    private List<String> tables;

    private int weight;
}