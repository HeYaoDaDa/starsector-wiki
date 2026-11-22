import { test, expect, type Page } from '@playwright/test';

/**
 * Starsector Wiki 冒烟测试
 *
 * 测试策略:
 * - 每个测试前后监听 console.error / pageerror，断言零错误
 * - 覆盖所有路由页面: 列表页 + 详情页
 * - 覆盖交互: 导航抽屉、语言切换、版本切换
 * - 覆盖边界: 404、不存在的 ID
 */

// ─── 辅助函数 ───────────────────────────────────────────

/** 等待应用数据加载完成（从 /load 重定向到首页） */
async function waitForAppReady(page: Page) {
  // 等待首页星图渲染出来（拿到任意一个 star system 链接）
  await expect(page.locator('a[href*="#/star_system/"]').first()).toBeVisible({
    timeout: 30_000,
  });
}

/** 打开导航抽屉并等待动画结束 */
async function openDrawer(page: Page) {
  await page.getByRole('button', { name: 'Menu' }).click();
  // 等 drawer 出现：检测 sidebar 的 list 是否可见
  await expect(page.locator('.q-drawer--left .q-list').first()).toBeVisible({ timeout: 5000 });
}

/** 关闭导航抽屉: 再次点击 Menu 按钮 */
async function closeDrawer(page: Page) {
  await page.getByRole('button', { name: 'Menu' }).click();
  // 等 drawer 动画结束
  await page.waitForTimeout(500);
}

/** 访问 hash 路由，等待 networkidle */
async function navigateTo(page: Page, hash: string) {
  await page.goto(hash);
  await page.waitForLoadState('networkidle');
}

// ─── 测试套件 ───────────────────────────────────────────

test.describe('Starsector Wiki 冒烟测试', () => {
  let errors: string[];
  let pageErrors: string[];

  test.beforeEach(async ({ page }) => {
    errors = [];
    pageErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(`[console error] ${msg.text()}`);
      }
    });
    page.on('pageerror', (err) => {
      pageErrors.push(`[page error] ${err.message}`);
    });
  });

  test.afterEach(async () => {
    const all = [...errors, ...pageErrors];
    expect(all).toEqual([]);
  });

  // ── 1. 首页加载 ────────────────────────────────────

  test('1. 首页加载 + 数据就绪', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // 标题正确
    await expect(page).toHaveTitle('Starsector Wiki');

    // 顶栏显示应用名称
    await expect(page.getByText('Starsector Wiki').first()).toBeVisible();

    // 版本选择器存在
    await expect(page.getByRole('button', { name: /0\.98/ })).toBeVisible();

    // 语言选择器存在
    await expect(page.getByRole('button', { name: 'English' })).toBeVisible();

    // 星图有 star system 链接
    const starLinks = page.locator('a[href*="#/star_system/"]');
    await expect(starLinks.first()).toBeVisible();
    const count = await starLinks.count();
    expect(count).toBeGreaterThan(15);
  });

  // ── 2. 导航抽屉 ────────────────────────────────────

  test('2. 导航抽屉: 打开/关闭 + 菜单项', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await openDrawer(page);

    // 检查关键菜单项
    const navLabels = [
      'Ships',
      'Ship Systems',
      'Hull Mods',
      'Weapons',
      'Special Items',
      'Commodities',
      'Industries',
      'Planet Types',
      'Market Conditions',
      'Submarket Types',
      'Factions',
      'Star Systems',
      'Planets',
      'Characters',
      'Quests & Dialogue',
    ];

    for (const label of navLabels) {
      await expect(page.getByText(label).first()).toBeVisible();
    }

    // 点击 Ships 跳转
    await page.getByText('Ships').click();
    await expect(page).toHaveURL(/#\/ships/);

    // 在 persistent 模式下抽屉不会自动关闭，手动关闭
    await closeDrawer(page);
  });

  // ── 3. 列表页面 ────────────────────────────────────

  /**
   * 页面可分为两类:
   * A) 有 "result-count" 文本的（ShipsDiv, FactionsDiv, IndustriesDiv, PlanetsDiv, PersonsDiv）
   * B) 无 result count，直接渲染 card-item 网格的（ShipSystemsPage, ShipModsPage, SpecialItemsPage,
   *    SubMarketsPage, CommoditesPage, PlanetTypesPage, MarketConditionsPage — 后者通过 MarketConditionsDiv 渲染）
   */

  // A) 带 result-count 的列表页
  const LIST_PAGES_WITH_COUNT = [
    { hash: '#/ships', detailPrefix: 'ships' },
    { hash: '#/weapons', detailPrefix: 'weapons' },
    { hash: '#/industries', detailPrefix: 'industry' },
    { hash: '#/market_conditions', detailPrefix: 'market_condition' },
    { hash: '#/factions', detailPrefix: 'faction' },
    { hash: '#/planets', detailPrefix: 'planet' },
    { hash: '#/persons', detailPrefix: 'person' },
  ];

  for (const { hash, detailPrefix } of LIST_PAGES_WITH_COUNT) {
    test(`3a. 列表页(有计数): ${hash}`, async ({ page }) => {
      await page.goto('/');
      await waitForAppReady(page);
      await navigateTo(page, hash);

      // 检查 result count
      await expect(page.locator('.result-count').first()).toBeVisible({ timeout: 10_000 });

      // 至少有一个数据条目（链接指向详情页）
      const items = page.locator(`a[href*="#/${detailPrefix}/"]`);
      const count = await items.count();
      expect(count).toBeGreaterThan(0);
    });
  }

  // B) 无 result-count 的列表页 —— 检查是否有 card-item 元素
  const LIST_PAGES_CARD_GRID = [
    { hash: '#/commodities', name: 'commodities' },
    { hash: '#/planet_types', name: 'planet types' },
    { hash: '#/sub_markets', name: 'sub markets' },
    { hash: '#/ship_systems', name: 'ship systems' },
    { hash: '#/ship_mods', name: 'ship mods' },
    { hash: '#/special_items', name: 'special items' },
  ];

  for (const { hash } of LIST_PAGES_CARD_GRID) {
    test(`3b. 列表页(卡片网格): ${hash}`, async ({ page }) => {
      await page.goto('/');
      await waitForAppReady(page);
      await navigateTo(page, hash);

      // 检查有卡片元素
      const cards = page.locator('.card-item');
      await expect(cards.first()).toBeVisible({ timeout: 10_000 });
      const count = await cards.count();
      expect(count).toBeGreaterThan(0);
    });
  }

  // 首页/恒星系图是特别情况: 直接检查链接数量
  test('3c. 首页恒星系图', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    const starLinks = page.locator('a[href*="#/star_system/"]');
    await expect(starLinks.first()).toBeVisible();
    const count = await starLinks.count();
    expect(count).toBeGreaterThan(15);
  });

  // ── 4. 详情页面 ────────────────────────────────────

  test('4a. 舰船详情页: Paragon', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/ships/paragon_Hull');

    // 标题
    await expect(page.getByText('Paragon-class Battleship').first()).toBeVisible();

    // 属性表格存在（至少有一行 td）
    await expect(page.locator('table td').first()).toBeVisible();

    // 应该有 variant loadouts 区域（h4 heading）
    await expect(page.locator('h4:has-text("Loadouts")')).toBeVisible();

    // 应该有 Factions 区域（h4 heading，不要匹配到侧边栏）
    await expect(page.locator('h4:has-text("Factions")')).toBeVisible();
  });

  test('4b. 舰船详情页: 不存在的 ID', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/ships/nonexistent_ship');

    // 应显示 not found 消息
    await expect(page.getByText(/not found/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('4c. 武器详情页: Light Dual Autocannon', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/weapons/lightdualac');

    // 标题
    await expect(page.getByText('Light Dual Autocannon').first()).toBeVisible();

    // 属性区存在
    await expect(page.getByText('Ordnance Points').first()).toBeVisible();

    // Used by Loadouts
    await expect(page.getByText('Used by Loadouts').first()).toBeVisible();
  });

  test('4d. 武器详情页: 不存在的 ID（验证错误消息）', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/weapons/arclight');

    await expect(page.getByText(/not found/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('4e. 派系详情页: Hegemony', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/faction/hegemony');

    // 标题
    await expect(page.getByText('Hegemony').first()).toBeVisible();

    // 应该有派系描述或其他内容
    await expect(page.locator('h4').first()).toBeVisible();
  });

  test('4f. 工业详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/industries');
    const firstLink = page.locator('a[href*="#/industry/"]').first();
    await expect(firstLink).toBeVisible({ timeout: 10_000 });
    const href = await firstLink.getAttribute('href');
    if (href) {
      await navigateTo(page, href);
      await expect(page.locator('h4').first()).toBeVisible();
    }
  });

  test('4g. 星球详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/planets');
    const firstLink = page.locator('a[href*="#/planet/"]').first();
    await expect(firstLink).toBeVisible({ timeout: 10_000 });
    const href = await firstLink.getAttribute('href');
    if (href) {
      await navigateTo(page, href);
      await expect(page.locator('h4').first()).toBeVisible();
    }
  });

  test('4h. 恒星系详情页: Corvus', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/star_system/corvus');

    // 应该有系统名称
    await expect(page.getByText('Corvus').first()).toBeVisible();
  });

  test('4i. 角色详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/persons');
    const firstLink = page.locator('a[href*="#/person/"]').first();
    await expect(firstLink).toBeVisible({ timeout: 10_000 });
    const href = await firstLink.getAttribute('href');
    if (href) {
      await navigateTo(page, href);
      await expect(page.locator('h4').first()).toBeVisible();
    }
  });

  test('4j. 特殊物品详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/special_items');
    const firstLink = page.locator('a[href*="#/special_item/"]').first();
    await expect(firstLink).toBeVisible({ timeout: 10_000 });
    const href = await firstLink.getAttribute('href');
    if (href) {
      await navigateTo(page, href);
      await expect(page.locator('h4').first()).toBeVisible();
    }
  });

  // ── 5. 语言切换 ────────────────────────────────────

  test('5. 语言切换: en → zh', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // 点击语言选择器
    await page.getByRole('button', { name: 'English' }).click();
    // 选择 "中文"
    await page.getByText('中文').click();

    // 等待页面 reload
    await page.waitForTimeout(1000);
    await waitForAppReady(page);

    // 导航栏应显示中文（使用 drawer 验证）
    await openDrawer(page);
    await expect(page.getByText('舰船').first()).toBeVisible();
    await expect(page.getByText('武器').first()).toBeVisible();
    await expect(page.getByText('派系').first()).toBeVisible();

    // 切回英文 — 先关掉中文 drawer
    await closeDrawer(page);
    // 语言按钮文字变成 "中文"
    await page.getByRole('button', { name: '中文' }).click();
    await page.getByText('English').click();
    await page.waitForTimeout(1000);
    await waitForAppReady(page);

    await openDrawer(page);
    await expect(page.getByText('Ships').first()).toBeVisible();
  });

  // ── 6. 404 页面 ────────────────────────────────────

  test('6. 404 页面', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/this_page_does_not_exist');

    // 应该显示 404
    await expect(page.getByText('404').first()).toBeVisible();
    await expect(page.getByText('Go Home').first()).toBeVisible();
  });

  // ── 7. 从列表页进入详情页 ──────────────────────────

  test('7. 从 Ships 列表点击进入详情', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);
    await navigateTo(page, '#/ships');

    // 找到第一个 ship 链接
    const shipLink = page.locator('a[href*="#/ships/"]').first();
    await expect(shipLink).toBeVisible({ timeout: 10_000 });
    const shipName = await shipLink.textContent();

    // 点击进入详情
    await shipLink.click();
    await page.waitForURL(/#\/ships\//);

    // 详情页标题应包含列表中的名字
    if (shipName) {
      await expect(page.getByText(shipName.trim()).first()).toBeVisible();
    }
  });

  // ── 8. 版本选择器 ──────────────────────────────────

  test('8. 版本选择器可用', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    // 版本按钮可见
    const versionBtn = page.getByRole('button', { name: /0\.98/ }).first();
    await expect(versionBtn).toBeVisible();

    // 点击展开
    await versionBtn.click();
    // 菜单项 "0.98a" 可见
    await expect(page.getByText('0.98a').first()).toBeVisible();
  });

  // ── 9. 响应式: 移动端视口（基础渲染） ──────────────

  test('9. 移动端视口基础渲染', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await waitForAppReady(page);

    // 标题正确
    await expect(page).toHaveTitle('Starsector Wiki');

    // 顶栏菜单按钮可见（移动端）
    await expect(page.getByRole('button', { name: 'Menu' }).first()).toBeVisible();

    // 在移动端应该有返回按钮 (lt-sm)
    await expect(page.getByRole('button', { name: 'Back' }).first()).toBeVisible();
  });

  // ── 10. 舰船系统详情页 ────────────────────────────

  test('10. 舰船系统详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/ship_systems');
    // 卡片网格中先找到第一个 card-item，获取里边的链接
    const firstCard = page.locator('.card-item').first();
    await expect(firstCard).toBeVisible({ timeout: 10_000 });
    await firstCard.click();
    await page.waitForURL(/\/ship_systems\//);
    await expect(page.locator('h4').first()).toBeVisible();
  });

  // ── 11. 舰船插件详情页 ────────────────────────────

  test('11. 舰船插件详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/ship_mods');
    const firstCard = page.locator('.card-item').first();
    await expect(firstCard).toBeVisible({ timeout: 10_000 });
    await firstCard.click();
    await page.waitForURL(/\/ship_mods\//);
    await expect(page.locator('h4').first()).toBeVisible();
  });

  // ── 12. 星球类型详情页 ────────────────────────────

  test('12. 星球类型详情页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/planet_types');
    const firstLink = page.locator('a[href*="#/planet_type/"]').first();
    await expect(firstLink).toBeVisible({ timeout: 10_000 });
    const href = await firstLink.getAttribute('href');
    if (href) {
      await navigateTo(page, href);
      await expect(page.locator('h4').first()).toBeVisible();
    }
  });

  // ── 13. 任务对话: 列表 + 详情 + 对话树交互 ──────────

  test('13a. 任务列表页', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/quests');
    const card = page.locator('.quest-card').first();
    await expect(card).toBeVisible({ timeout: 10_000 });
    // 至少包含任务名与阶段计数
    await expect(card.getByText('The Usurpers')).toBeVisible();
  });

  test('13b. 任务详情 + 对话树交互', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/quests/the_usurpers');
    // 任务阶段与人物渲染
    await expect(page.locator('.quest-stage').first()).toBeVisible({ timeout: 10_000 });
    expect(await page.locator('.quest-stage').count()).toBeGreaterThan(5);
    expect(await page.locator('.quest-character').count()).toBeGreaterThan(3);

    // 打开第一个对话场景
    await expect(page.locator('.quest-scene-btn').first()).toBeVisible();
    await page.locator('.quest-scene-btn').first().click();
    await expect(page.locator('.quest-dialogue')).toBeVisible({ timeout: 10_000 });

    // 触发条件面板（入口步骤）
    await expect(page.locator('.dlg-entry-conds').first()).toBeVisible();

    // 点击第一个可用选项，路径芯片应增加
    const option = page.locator('.dlg-option:not([disabled])').first();
    await expect(option).toBeVisible();
    await option.click();
    const chips = page.locator('.dlg-path .q-chip');
    await expect(chips.first()).toBeVisible({ timeout: 10_000 });
    expect(await chips.count()).toBeGreaterThan(0);

    // 点击路径芯片可回溯
    await chips.first().click();
  });

  test('13c. 任务详情: 不存在的任务 ID', async ({ page }) => {
    await page.goto('/');
    await waitForAppReady(page);

    await navigateTo(page, '#/quests/no_such_quest');
    await expect(page.getByText(/not found/i).first()).toBeVisible({ timeout: 10_000 });
  });
});
