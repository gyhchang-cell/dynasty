package com.provismet.dualswords.enchantments;

public class ParryEnchantment extends AbstractParryTypeEnchantment {
    public ParryEnchantment () {
        super(Rarity.UNCOMMON);
    }

    @Override
    public int getMaxLevel () {
        return 3;
    }

    @Override
    public int getMinPower(int level) {
        return 5 + 10 * (level - 1);
    }

    @Override
    public int getMaxPower(int level) {
        return this.getMinPower(level) + 50;
    }
}
