/*
 * This file is part of pnc-repressurized.
 *
 *     pnc-repressurized is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 *
 *     pnc-repressurized is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with pnc-repressurized.  If not, see <https://www.gnu.org/licenses/>.
 */

package me.desht.pneumaticcraft.common.thirdparty.immersiveengineering;

import me.desht.pneumaticcraft.common.registry.ModHarvestHandlers;
import me.desht.pneumaticcraft.common.thirdparty.IThirdParty;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;

import java.util.function.Supplier;

public class ImmersiveEngineering implements IThirdParty {
    @SuppressWarnings("unused")
    public static final Supplier<HempHarvestHandler> HEMP_HARVEST
            = ModHarvestHandlers.register("ie_hemp", HempHarvestHandler::new);

    @Override
    public void preInit(IEventBus modBus) {
        NeoForge.EVENT_BUS.addListener(ElectricAttackHandler::onElectricalAttack);
        modBus.addListener(IEHeatHandler::registerCap);
    }
}
