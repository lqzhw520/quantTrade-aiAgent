describe('股票指标计算可视化', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('选择股票和日期后自动拉取并渲染指标图表', () => {
    // 选择股票
    cy.get('[data-cy=stock-select]').click().type(' ');
    cy.get('body').find('.el-select-dropdown__item', { timeout: 10000 }).should('be.visible');
    cy.get('body').find('.el-select-dropdown__item').contains('万科A').click();

    // 选择开始日期
    cy.get('[data-cy=start-date]').find('input').clear().type('2025-01-01');
    // 选择结束日期
    cy.get('[data-cy=end-date]').find('input').clear().type('2025-05-15');

    // 等待接口请求和渲染
    cy.get('[data-cy=indicator-chart]', { timeout: 10000 }).should('exist');
    cy.get('[data-cy=no-data-message]').should('not.exist');
  });

  it('选择无数据区间时显示暂无数据', () => {
    // 选择股票
    cy.get('[data-cy=stock-select]').click().type(' ');
    cy.get('body').find('.el-select-dropdown__item', { timeout: 10000 }).should('be.visible');
    cy.get('body').find('.el-select-dropdown__item').contains('万科A').click();

    // 选择未来日期
    cy.get('[data-cy=start-date]').find('input').clear().type('2099-01-01');
    cy.get('[data-cy=end-date]').find('input').clear().type('2099-05-15');

    cy.get('[data-cy=indicator-chart]').should('not.exist');
    cy.get('[data-cy=no-data-message]', { timeout: 10000 }).should('exist');
  });

  it('开始日期晚于结束日期时前端校验', () => {
    // 选择股票
    cy.get('[data-cy=stock-select]').click().type(' ');
    cy.get('body').find('.el-select-dropdown__item', { timeout: 10000 }).should('be.visible');
    cy.get('body').find('.el-select-dropdown__item').contains('万科A').click();

    // 选择错误日期
    cy.get('[data-cy=start-date]').find('input').clear().type('2025-05-15');
    cy.get('[data-cy=end-date]').find('input').clear().type('2025-01-01');

    cy.get('.el-alert').should('contain', '开始日期不能晚于结束日期');
  });
}); 